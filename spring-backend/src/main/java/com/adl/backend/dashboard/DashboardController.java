package com.adl.backend.dashboard;

import com.adl.backend.dashboard.dto.DashboardDtos;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    @GetMapping("/overview/national")
    public ResponseEntity<DashboardDtos.NationalOverviewDto> getNationalOverview() {
        return ResponseEntity.ok(dashboardService.getNationalOverview(LocalDate.now()));
    }

    @GetMapping("/production/regions")
    public ResponseEntity<List<DashboardDtos.RegionProductionDto>> getRegionProduction(
            @RequestParam(name = "startDate", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(name = "endDate", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate
    ) {
        return ResponseEntity.ok(dashboardService.getRegionProduction(startDate, endDate));
    }

    @GetMapping("/prices/markets")
    public ResponseEntity<List<DashboardDtos.MarketPriceDto>> getMarketPrices(
            @RequestParam(name = "date", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        return ResponseEntity.ok(dashboardService.getMarketPrices(date));
    }

    @GetMapping("/prices/volatility")
    public ResponseEntity<List<DashboardDtos.PriceVolatilityDto>> getPriceVolatility(
            @RequestParam(name = "startDate", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(name = "endDate", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate
    ) {
        return ResponseEntity.ok(dashboardService.getPriceVolatility(startDate, endDate));
    }

    @GetMapping("/storage/warehouses")
    public ResponseEntity<List<DashboardDtos.StorageWarehouseDto>> getStorageWarehouses(
            @RequestParam(name = "date", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        return ResponseEntity.ok(dashboardService.getStorageWarehouses(date));
    }

    @GetMapping("/storage/utilization")
    public ResponseEntity<DashboardDtos.StorageUtilizationDto> getStorageUtilization(
            @RequestParam(name = "date", required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        return ResponseEntity.ok(dashboardService.getStorageUtilization(date));
    }

    @GetMapping("/seasonality/monthly")
    public ResponseEntity<List<DashboardDtos.SeasonalityMonthlyDto>> getSeasonalityMonthly(
            @RequestParam(name = "year", required = false) Integer year
    ) {
        int targetYear = year != null ? year : LocalDate.now().getYear();
        return ResponseEntity.ok(dashboardService.getSeasonalityMonthly(targetYear));
    }

    @GetMapping("/forecast/production")
    public ResponseEntity<List<DashboardDtos.ProductionForecastDto>> getProductionForecast(
            @RequestParam(name = "regionCode") String regionCode,
            @RequestParam(name = "months", required = false) Integer months
    ) {
        int horizon = months != null ? months : 6;
        return ResponseEntity.ok(dashboardService.getProductionForecast(regionCode, horizon));
    }

    @GetMapping("/forecast/prices")
    public ResponseEntity<List<DashboardDtos.PriceForecastDto>> getPriceForecast(
            @RequestParam(name = "market") String market,
            @RequestParam(name = "months", required = false) Integer months
    ) {
        int horizon = months != null ? months : 3;
        return ResponseEntity.ok(dashboardService.getPriceForecast(market, horizon));
    }

    @GetMapping("/forecast/model-metrics")
    public ResponseEntity<DashboardDtos.ModelMetricsDto> getModelMetrics() {
        return ResponseEntity.ok(dashboardService.getModelMetrics());
    }

    @GetMapping("/forecast/model-metadata")
    public ResponseEntity<DashboardDtos.ModelMetadataDto> getModelMetadata() {
        return ResponseEntity.ok(dashboardService.getModelMetadata());
    }
}
