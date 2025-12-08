package com.adl.backend.persistence.repository;

import com.adl.backend.persistence.entity.StorageData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface StorageDataRepository extends JpaRepository<StorageData, Long> {

    interface WarehouseAggregate {
        String getWarehouse();
        Double getCapacity();
        Double getQuantity();
        String getRegionCode();
    }

    @Query("select s.warehouse as warehouse, s.capacity as capacity, s.quantity as quantity, r.code as regionCode from StorageData s join s.region r where s.date = :date")
    List<WarehouseAggregate> latestForDate(@Param("date") LocalDate date);

    @Query("select coalesce(sum(s.capacity),0), coalesce(sum(s.quantity),0) from StorageData s where s.date = :date")
    List<Object[]> aggregateTotalsForDate(@Param("date") LocalDate date);
}
