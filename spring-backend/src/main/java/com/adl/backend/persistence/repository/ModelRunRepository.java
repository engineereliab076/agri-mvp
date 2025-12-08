package com.adl.backend.persistence.repository;

import com.adl.backend.persistence.entity.ModelRun;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ModelRunRepository extends JpaRepository<ModelRun, Long> {
}
