package com.adl.backend.persistence.repository;

import com.adl.backend.persistence.entity.ProductionData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Repository
public interface ProductionDataRepository extends JpaRepository<ProductionData, Long> {

    interface RegionProductionAggregate {
        String getRegionCode();
        BigDecimal getTotalQuantity();
    }

    @Query("select r.code as regionCode, sum(p.quantity) as totalQuantity " +
            "from ProductionData p join p.region r " +
            "where p.date between :start and :end " +
            "group by r.code")
    List<RegionProductionAggregate> aggregateByRegion(@Param("start") LocalDate start, @Param("end") LocalDate end);

    @Query("select sum(p.quantity) from ProductionData p where p.date between :start and :end")
    BigDecimal sumQuantityBetween(@Param("start") LocalDate start, @Param("end") LocalDate end);
}
