package com.adl.backend.auth;

import com.adl.backend.auth.dto.AuthDtos;

public interface AuthService {
    AuthDtos.AuthResponse signup(AuthDtos.SignupRequest request);
    AuthDtos.AuthResponse login(AuthDtos.LoginRequest request);
}
