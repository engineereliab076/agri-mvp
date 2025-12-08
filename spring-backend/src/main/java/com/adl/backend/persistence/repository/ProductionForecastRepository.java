package com.adl.backend.persistence.repository;

import com.adl.backend.persistence.entity.ProductionForecast;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface ProductionForecastRepository extends JpaRepository<ProductionForecast, Long> {
    List<ProductionForecast> findByRegion_CodeAndDateGreaterThanEqualOrderByDateAsc(String code, LocalDate startDate);
}
