package com.adl.backend.persistence.repository;

import com.adl.backend.persistence.entity.PriceForecast;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface PriceForecastRepository extends JpaRepository<PriceForecast, Long> {
    List<PriceForecast> findByMarketAndDateGreaterThanEqualOrderByDateAsc(String market, LocalDate startDate);
}
