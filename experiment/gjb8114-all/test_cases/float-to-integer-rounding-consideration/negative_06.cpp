int applyScale(double factor) {
    return factor * 10.0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
}

int main() {
    return applyScale(3.25) > 0 ? 0 : 1;
}
