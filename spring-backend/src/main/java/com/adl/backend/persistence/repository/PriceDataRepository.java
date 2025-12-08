package com.adl.backend.persistence.repository;

import com.adl.backend.persistence.entity.PriceData;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Repository
public interface PriceDataRepository extends JpaRepository<PriceData, Long> {

    interface MarketPriceAggregate {
        String getMarket();
        BigDecimal getAveragePrice();
    }

    @Query("select p.market as market, avg(p.price) as averagePrice " +
            "from PriceData p " +
            "where p.date = :date " +
            "group by p.market")
    List<MarketPriceAggregate> averagePriceByMarket(@Param("date") LocalDate date);

    @Query("select p.market as market, avg(p.price) as averagePrice " +
            "from PriceData p " +
            "where p.date between :start and :end " +
            "group by p.market")
    List<MarketPriceAggregate> averagePriceByMarketBetween(@Param("start") LocalDate start, @Param("end") LocalDate end);

    @Query("select p.price from PriceData p where p.market = :market and p.date between :start and :end")
    List<BigDecimal> pricesForMarketBetween(@Param("market") String market, @Param("start") LocalDate start, @Param("end") LocalDate end);

    @Query("select avg(p.price) from PriceData p where p.date between :start and :end")
    BigDecimal averagePriceBetween(@Param("start") LocalDate start, @Param("end") LocalDate end);
}
