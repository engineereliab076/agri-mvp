package com.adl.backend.dashboard.dto;

import java.time.LocalDate;
import java.util.List;

public class DashboardDtos {

    public record NationalOverviewDto(
            double totalProduction,
            double averagePrice,
            double storageUtilizationPercent,
            double productionChangePercent
    ) {
    }

    public record RegionProductionDto(
            String regionCode,
            String regionName,
            double totalQuantity
    ) {
    }

    public record MarketPriceDto(
            String market,
            double averagePrice
    ) {
    }

    public record PriceVolatilityDto(
            String market,
            double volatility
    ) {
    }

    public record StorageWarehouseDto(
            String warehouse,
            String regionCode,
            double capacity,
            double quantity,
            double utilizationPercent
    ) {
    }

    public record StorageUtilizationDto(
            double totalCapacity,
            double totalQuantity,
            double utilizationPercent
    ) {
    }

    public record SeasonalityMonthlyDto(
            int year,
            int month,
            double totalProduction
    ) {
    }

    public record ProductionForecastDto(
            String regionCode,
            LocalDate date,
            double forecastValue,
            double lowerBound,
            double upperBound
    ) {
    }

    public record PriceForecastDto(
            String market,
            LocalDate date,
            double forecastValue,
            double lowerBound,
            double upperBound
    ) {
    }

    public record ModelMetricsDto(
            String modelName,
            String modelVersion,
            double mae,
            double rmse,
            double mape,
            String confidenceLevel
    ) {
    }

    public record ModelMetadataDto(
            String modelName,
            String modelVersion,
            List<String> features
    ) {
    }
}
