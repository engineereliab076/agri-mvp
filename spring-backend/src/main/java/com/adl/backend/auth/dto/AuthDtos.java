package com.adl.backend.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.time.LocalDate;
import java.util.Set;

public class AuthDtos {

    public record LoginRequest(
            @NotBlank String username,
            @NotBlank String password
    ) {
    }

    public record SignupRequest(
            @NotBlank @Size(min = 3, max = 80) String username,
            @NotBlank @Email String email,
            @NotBlank @Size(min = 6, max = 100) String password,
            String firstName,
            String lastName,
            String nationalId,
            String phone,
            String address,
            LocalDate dateOfBirth,
            String companyName,
            String companyRegistrationNumber,
            String companyTin,
            String companyAddress
    ) {
    }

    public record AuthResponse(
            String accessToken,
            String tokenType,
            long expiresInSeconds,
            String username,
            Set<String> roles
    ) {
    }
}
