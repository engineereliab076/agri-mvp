package com.adl.backend.auth;

import com.adl.backend.auth.dto.AuthDtos;
import com.adl.backend.security.util.JwtTokenProvider;
import com.adl.backend.user.Role;
import com.adl.backend.user.RoleName;
import com.adl.backend.user.RoleRepository;
import com.adl.backend.user.User;
import com.adl.backend.user.UserRepository;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

@Service
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider tokenProvider;

    public AuthServiceImpl(UserRepository userRepository,
                           RoleRepository roleRepository,
                           PasswordEncoder passwordEncoder,
                           AuthenticationManager authenticationManager,
                           JwtTokenProvider tokenProvider) {
        this.userRepository = userRepository;
        this.roleRepository = roleRepository;
        this.passwordEncoder = passwordEncoder;
        this.authenticationManager = authenticationManager;
        this.tokenProvider = tokenProvider;
    }

    @Override
    @Transactional
    public AuthDtos.AuthResponse signup(AuthDtos.SignupRequest request) {
        if (userRepository.existsByUsername(request.username())) {
            throw new IllegalArgumentException("Username already exists");
        }
        if (userRepository.existsByEmail(request.email())) {
            throw new IllegalArgumentException("Email already exists");
        }
        User user = new User();
        user.setUsername(request.username());
        user.setEmail(request.email());
        user.setPassword(passwordEncoder.encode(request.password()));
        user.setFirstName(request.firstName());
        user.setLastName(request.lastName());
        user.setNationalId(request.nationalId());
        user.setPhone(request.phone());
        user.setAddress(request.address());
        user.setDateOfBirth(request.dateOfBirth());
        user.setCompanyName(request.companyName());
        user.setCompanyRegistrationNumber(request.companyRegistrationNumber());
        user.setCompanyTin(request.companyTin());
        user.setCompanyAddress(request.companyAddress());
        Role defaultRole = roleRepository.findByName(RoleName.ROLE_VIEWER).orElseThrow(() -> new IllegalStateException("Default role not found"));
        Set<Role> roles = new HashSet<>();
        roles.add(defaultRole);
        user.setRoles(roles);
        userRepository.save(user);
        Authentication authentication = authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(request.username(), request.password()));
        String token = tokenProvider.generateToken(authentication);
        Set<String> roleNames = user.getRoles().stream().map(r -> r.getName().name()).collect(Collectors.toSet());
        long expiresInSeconds = tokenProvider.getExpirationHours() * 3600;
        return new AuthDtos.AuthResponse(token, "Bearer", expiresInSeconds, user.getUsername(), roleNames);
    }

    @Override
    public AuthDtos.AuthResponse login(AuthDtos.LoginRequest request) {
        Authentication authentication = authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(request.username(), request.password()));
        String token = tokenProvider.generateToken(authentication);
        User user = userRepository.findByUsername(request.username()).orElseThrow(() -> new IllegalArgumentException("Invalid credentials"));
        Set<String> roleNames = user.getRoles().stream().map(r -> r.getName().name()).collect(Collectors.toSet());
        long expiresInSeconds = tokenProvider.getExpirationHours() * 3600;
        return new AuthDtos.AuthResponse(token, "Bearer", expiresInSeconds, user.getUsername(), roleNames);
    }
}
