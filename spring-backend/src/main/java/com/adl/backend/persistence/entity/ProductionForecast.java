package com.adl.backend.persistence.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Objects;

@Entity
@Table(name = "production_forecast")
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ProductionForecast {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(optional = false, fetch = FetchType.LAZY)
    @JoinColumn(name = "region_id")
    private Region region;

    @Column(nullable = false)
    private LocalDate date;

    @Column(name = "forecast_value", nullable = false, precision = 19, scale = 2)
    private BigDecimal forecastValue;

    @Column(name = "lower_bound", precision = 19, scale = 2)
    private BigDecimal lowerBound;

    @Column(name = "upper_bound", precision = 19, scale = 2)
    private BigDecimal upperBound;

    @ManyToOne(optional = false, fetch = FetchType.LAZY)
    @JoinColumn(name = "model_run_id")
    private ModelRun modelRun;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ProductionForecast)) return false;
        ProductionForecast that = (ProductionForecast) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
