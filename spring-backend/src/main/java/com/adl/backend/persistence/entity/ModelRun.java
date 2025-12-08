package com.adl.backend.persistence.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "model_run")
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ModelRun {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "model_name", nullable = false, length = 100)
    private String modelName;

    @Column(name = "model_version", nullable = false, length = 50)
    private String modelVersion;

    @Column(name = "run_at", nullable = false)
    private LocalDateTime runAt;

    @Column(name = "mae")
    private Double mae;

    @Column(name = "rmse")
    private Double rmse;

    @Column(name = "mape")
    private Double mape;

    @Column(name = "confidence_level", length = 20)
    private String confidenceLevel;


}
