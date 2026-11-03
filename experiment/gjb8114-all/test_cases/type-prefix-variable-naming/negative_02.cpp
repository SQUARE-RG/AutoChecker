int computeAzimuth(double azimuth) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-1]
    return static_cast<int>(azimuth);
}

int main() {
    return computeAzimuth(0.0);
}
