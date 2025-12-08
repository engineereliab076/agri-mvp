package com.adl.backend.dashboard;

import com.adl.backend.dashboard.dto.DashboardDtos;

import java.time.LocalDate;
import java.util.List;

public interface DashboardService {

    DashboardDtos.NationalOverviewDto getNationalOverview(LocalDate now);

    List<DashboardDtos.RegionProductionDto> getRegionProduction(LocalDate startDate, LocalDate endDate);

    List<DashboardDtos.MarketPriceDto> getMarketPrices(LocalDate date);

    List<DashboardDtos.PriceVolatilityDto> getPriceVolatility(LocalDate startDate, LocalDate endDate);

    List<DashboardDtos.StorageWarehouseDto> getStorageWarehouses(LocalDate date);

    DashboardDtos.StorageUtilizationDto getStorageUtilization(LocalDate date);

    List<DashboardDtos.SeasonalityMonthlyDto> getSeasonalityMonthly(int year);

    List<DashboardDtos.ProductionForecastDto> getProductionForecast(String regionCode, int months);

    List<DashboardDtos.PriceForecastDto> getPriceForecast(String market, int months);

    DashboardDtos.ModelMetricsDto getModelMetrics();

    DashboardDtos.ModelMetadataDto getModelMetadata();
}
