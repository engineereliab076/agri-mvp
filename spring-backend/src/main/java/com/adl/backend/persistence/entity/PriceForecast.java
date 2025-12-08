package com.adl.backend.persistence.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "price_forecast")
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class PriceForecast {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 120)
    private String market;

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


}
