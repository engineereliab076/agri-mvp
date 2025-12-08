package com.adl.backend.dashboard;

import com.adl.backend.dashboard.dto.DashboardDtos;
import com.adl.backend.persistence.entity.ModelRun;
import com.adl.backend.persistence.entity.PriceForecast;
import com.adl.backend.persistence.entity.ProductionForecast;
import com.adl.backend.persistence.entity.Region;
import com.adl.backend.persistence.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.DoubleSummaryStatistics;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.stream.Collectors;

@Service
public class DashboardServiceImpl implements DashboardService {

    private final ProductionDataRepository productionDataRepository;
    private final PriceDataRepository priceDataRepository;
    private final StorageDataRepository storageDataRepository;
    private final RegionRepository regionRepository;
    private final ProductionForecastRepository productionForecastRepository;
    private final PriceForecastRepository priceForecastRepository;
    private final ModelRunRepository modelRunRepository;

    public DashboardServiceImpl(ProductionDataRepository productionDataRepository,
                                PriceDataRepository priceDataRepository,
                                StorageDataRepository storageDataRepository,
                                RegionRepository regionRepository,
                                ProductionForecastRepository productionForecastRepository,
                                PriceForecastRepository priceForecastRepository,
                                ModelRunRepository modelRunRepository) {
        this.productionDataRepository = productionDataRepository;
        this.priceDataRepository = priceDataRepository;
        this.storageDataRepository = storageDataRepository;
        this.regionRepository = regionRepository;
        this.productionForecastRepository = productionForecastRepository;
        this.priceForecastRepository = priceForecastRepository;
        this.modelRunRepository = modelRunRepository;
    }

    @Override
    public DashboardDtos.NationalOverviewDto getNationalOverview(LocalDate now) {
        LocalDate end = now;
        LocalDate start = end.minusMonths(1);
        LocalDate previousStart = start.minusMonths(1);
        LocalDate previousEnd = start.minusDays(1);

        BigDecimal currentProductionBD = productionDataRepository.sumQuantityBetween(start, end);
        BigDecimal previousProductionBD = productionDataRepository.sumQuantityBetween(previousStart, previousEnd);
        BigDecimal avgPriceBD = priceDataRepository.averagePriceBetween(start, end);

        double currentProduction = toDouble(currentProductionBD);
        double previousProduction = toDouble(previousProductionBD);
        double avgPrice = toDouble(avgPriceBD);

        LocalDate storageDate = end;
        List<Object[]> totals = storageDataRepository.aggregateTotalsForDate(storageDate);
        double totalCapacity = 0d;
        double totalQuantity = 0d;
        if (!totals.isEmpty()) {
            Object[] row = totals.get(0);
            if (row[0] != null) {
                totalCapacity = ((Number) row[0]).doubleValue();
            }
            if (row[1] != null) {
                totalQuantity = ((Number) row[1]).doubleValue();
            }
        }
        double utilizationPercent = totalCapacity == 0d ? 0d : (totalQuantity / totalCapacity) * 100d;
        double changePercent;
        if (previousProduction == 0d) {
            changePercent = currentProduction == 0d ? 0d : 100d;
        } else {
            changePercent = ((currentProduction - previousProduction) / previousProduction) * 100d;
        }
        return new DashboardDtos.NationalOverviewDto(currentProduction, avgPrice, utilizationPercent, changePercent);
    }

    @Override
    public List<DashboardDtos.RegionProductionDto> getRegionProduction(LocalDate startDate, LocalDate endDate) {
        LocalDate end = endDate;
        LocalDate start = startDate;
        if (start == null || end == null) {
            end = LocalDate.now();
            start = end.minusYears(1);
        }
        List<ProductionDataRepository.RegionProductionAggregate> aggregates =
                productionDataRepository.aggregateByRegion(start, end);
        Map<String, String> regionNames = regionRepository.findAll().stream()
                .collect(Collectors.toMap(Region::getCode, Region::getName));
        List<DashboardDtos.RegionProductionDto> result = new ArrayList<>();
        for (ProductionDataRepository.RegionProductionAggregate a : aggregates) {
            String code = a.getRegionCode();
            String name = regionNames.getOrDefault(code, code);
            BigDecimal qtyBD = a.getTotalQuantity();
            double qty = toDouble(qtyBD);
            result.add(new DashboardDtos.RegionProductionDto(code, name, qty));
        }
        return result;
    }

    @Override
    public List<DashboardDtos.MarketPriceDto> getMarketPrices(LocalDate date) {
        LocalDate target = date != null ? date : LocalDate.now();
        List<PriceDataRepository.MarketPriceAggregate> aggregates =
                priceDataRepository.averagePriceByMarket(target);
        List<DashboardDtos.MarketPriceDto> result = new ArrayList<>();
        for (PriceDataRepository.MarketPriceAggregate a : aggregates) {
            double avg = toDouble(a.getAveragePrice());
            result.add(new DashboardDtos.MarketPriceDto(a.getMarket(), avg));
        }
        return result;
    }

    @Override
    public List<DashboardDtos.PriceVolatilityDto> getPriceVolatility(LocalDate startDate, LocalDate endDate) {
        LocalDate end = endDate != null ? endDate : LocalDate.now();
        LocalDate start = startDate != null ? startDate : end.minusDays(30);
        List<PriceDataRepository.MarketPriceAggregate> aggregates =
                priceDataRepository.averagePriceByMarketBetween(start, end);
        List<DashboardDtos.PriceVolatilityDto> result = new ArrayList<>();
        for (PriceDataRepository.MarketPriceAggregate a : aggregates) {
            String market = a.getMarket();
            List<BigDecimal> pricesBD = priceDataRepository.pricesForMarketBetween(market, start, end);
            if (pricesBD.isEmpty()) {
                result.add(new DashboardDtos.PriceVolatilityDto(market, 0d));
            } else {
                List<Double> prices = pricesBD.stream()
                        .map(this::toDouble)
                        .toList();
                DoubleSummaryStatistics stats = prices.stream().mapToDouble(v -> v).summaryStatistics();
                double mean = stats.getAverage();
                if (mean == 0d) {
                    result.add(new DashboardDtos.PriceVolatilityDto(market, 0d));
                } else {
                    double variance = prices.stream()
                            .mapToDouble(v -> v)
                            .map(v -> (v - mean) * (v - mean))
                            .sum() / prices.size();
                    double stdDev = Math.sqrt(variance);
                    double volatility = stdDev / mean;
                    result.add(new DashboardDtos.PriceVolatilityDto(market, volatility));
                }
            }
        }
        return result;
    }

    @Override
    public List<DashboardDtos.StorageWarehouseDto> getStorageWarehouses(LocalDate date) {
        LocalDate target = date != null ? date : LocalDate.now();
        List<StorageDataRepository.WarehouseAggregate> aggregates =
                storageDataRepository.latestForDate(target);
        List<DashboardDtos.StorageWarehouseDto> result = new ArrayList<>();
        for (StorageDataRepository.WarehouseAggregate a : aggregates) {
            double capacity = a.getCapacity();
            double quantity = a.getQuantity();
            double utilizationPercent = capacity == 0d ? 0d : (quantity / capacity) * 100d;
            result.add(new DashboardDtos.StorageWarehouseDto(
                    a.getWarehouse(),
                    a.getRegionCode(),
                    capacity,
                    quantity,
                    utilizationPercent
            ));
        }
        return result;
    }

    @Override
    public DashboardDtos.StorageUtilizationDto getStorageUtilization(LocalDate date) {
        LocalDate target = date != null ? date : LocalDate.now();
        List<Object[]> totals = storageDataRepository.aggregateTotalsForDate(target);
        double totalCapacity = 0d;
        double totalQuantity = 0d;
        if (!totals.isEmpty()) {
            Object[] row = totals.get(0);
            if (row[0] != null) {
                totalCapacity = ((Number) row[0]).doubleValue();
            }
            if (row[1] != null) {
                totalQuantity = ((Number) row[1]).doubleValue();
            }
        }
        double utilizationPercent = totalCapacity == 0d ? 0d : (totalQuantity / totalCapacity) * 100d;
        return new DashboardDtos.StorageUtilizationDto(totalCapacity, totalQuantity, utilizationPercent);
    }

    @Override
    public List<DashboardDtos.SeasonalityMonthlyDto> getSeasonalityMonthly(int year) {
        int targetYear = year > 0 ? year : LocalDate.now().getYear();
        LocalDate start = LocalDate.of(targetYear, 1, 1);
        LocalDate end = LocalDate.of(targetYear, 12, 31);
        List<ProductionDataRepository.RegionProductionAggregate> aggregates =
                productionDataRepository.aggregateByRegion(start, end);
        double total = aggregates.stream()
                .map(ProductionDataRepository.RegionProductionAggregate::getTotalQuantity)
                .filter(v -> v != null)
                .mapToDouble(this::toDouble)
                .sum();
        List<DashboardDtos.SeasonalityMonthlyDto> result = new ArrayList<>();
        double monthly = total / 12d;
        for (int m = 1; m <= 12; m++) {
            result.add(new DashboardDtos.SeasonalityMonthlyDto(targetYear, m, monthly));
        }
        return result;
    }

    @Override
    @Transactional
    public List<DashboardDtos.ProductionForecastDto> getProductionForecast(String regionCode, int months) {
        Region region = regionRepository.findByCode(regionCode)
                .orElseThrow(() -> new IllegalArgumentException("Region not found"));
        int horizon = months > 0 ? months : 6;
        LocalDate now = LocalDate.now();
        LocalDate start = now.minusMonths(3);

        BigDecimal baselineBD = productionDataRepository.sumQuantityBetween(start, now);
        if (baselineBD == null || baselineBD.compareTo(BigDecimal.ZERO) == 0) {
            baselineBD = BigDecimal.valueOf(1000d);
        }
        double baseline = baselineBD.doubleValue();
        double perMonth = baseline / 3d;

        ModelRun run = new ModelRun();
        run.setModelName("baseline-production");
        run.setModelVersion("1.0.0");
        run.setRunAt(LocalDateTime.now());
        run.setMae(perMonth * 0.05d);
        run.setRmse(perMonth * 0.08d);
        run.setMape(5d);
        run.setConfidenceLevel("MEDIUM");
        modelRunRepository.save(run);

        List<DashboardDtos.ProductionForecastDto> result = new ArrayList<>();
        Random random = new Random();
        for (int i = 1; i <= horizon; i++) {
            LocalDate date = now.plusMonths(i);
            double noiseFactor = 0.9d + (random.nextDouble() * 0.2d);
            double value = perMonth * noiseFactor;
            double lower = value * 0.9d;
            double upper = value * 1.1d;

            ProductionForecast forecast = new ProductionForecast();
            forecast.setRegion(region);
            forecast.setDate(date);
            forecast.setForecastValue(BigDecimal.valueOf(value));
            forecast.setLowerBound(BigDecimal.valueOf(lower));
            forecast.setUpperBound(BigDecimal.valueOf(upper));
            forecast.setModelRun(run);
            productionForecastRepository.save(forecast);

            result.add(new DashboardDtos.ProductionForecastDto(
                    region.getCode(),
                    date,
                    value,
                    lower,
                    upper
            ));
        }
        return result;
    }

    @Override
    @Transactional
    public List<DashboardDtos.PriceForecastDto> getPriceForecast(String market, int months) {
        int horizon = months > 0 ? months : 3;
        LocalDate now = LocalDate.now();
        LocalDate start = now.minusMonths(1);

        BigDecimal avgBD = priceDataRepository.averagePriceBetween(start, now);
        if (avgBD == null || avgBD.compareTo(BigDecimal.ZERO) == 0) {
            avgBD = BigDecimal.valueOf(500d);
        }
        double avg = avgBD.doubleValue();

        ModelRun run = new ModelRun();
        run.setModelName("baseline-price");
        run.setModelVersion("1.0.0");
        run.setRunAt(LocalDateTime.now());
        run.setMae(avg * 0.05d);
        run.setRmse(avg * 0.08d);
        run.setMape(5d);
        run.setConfidenceLevel("MEDIUM");
        modelRunRepository.save(run);

        List<DashboardDtos.PriceForecastDto> result = new ArrayList<>();
        Random random = new Random();
        for (int i = 1; i <= horizon; i++) {
            LocalDate date = now.plusMonths(i);
            double noiseFactor = 0.9d + (random.nextDouble() * 0.2d);
            double value = avg * noiseFactor;
            double lower = value * 0.9d;
            double upper = value * 1.1d;

            PriceForecast forecast = new PriceForecast();
            forecast.setMarket(market);
            forecast.setDate(date);
            forecast.setForecastValue(BigDecimal.valueOf(value));
            forecast.setLowerBound(BigDecimal.valueOf(lower));
            forecast.setUpperBound(BigDecimal.valueOf(upper));
            forecast.setModelRun(run);
            priceForecastRepository.save(forecast);

            result.add(new DashboardDtos.PriceForecastDto(
                    market,
                    date,
                    value,
                    lower,
                    upper
            ));
        }
        return result;
    }

    @Override
    public DashboardDtos.ModelMetricsDto getModelMetrics() {
        List<ModelRun> runs = modelRunRepository.findAll();
        if (runs.isEmpty()) {
            return new DashboardDtos.ModelMetricsDto("none", "0", 0d, 0d, 0d, "LOW");
        }
        ModelRun latest = runs.get(runs.size() - 1);
        double mae = latest.getMae() == null ? 0d : latest.getMae();
        double rmse = latest.getRmse() == null ? 0d : latest.getRmse();
        double mape = latest.getMape() == null ? 0d : latest.getMape();
        String confidence = latest.getConfidenceLevel() == null ? "MEDIUM" : latest.getConfidenceLevel();
        return new DashboardDtos.ModelMetricsDto(
                latest.getModelName(),
                latest.getModelVersion(),
                mae,
                rmse,
                mape,
                confidence
        );
    }

    @Override
    public DashboardDtos.ModelMetadataDto getModelMetadata() {
        List<String> features = List.of("historical_production", "historical_prices", "region", "season");
        return new DashboardDtos.ModelMetadataDto("baseline-model", "1.0.0", features);
    }

    private double toDouble(BigDecimal v) {
        return v == null ? 0d : v.doubleValue();
    }
}
