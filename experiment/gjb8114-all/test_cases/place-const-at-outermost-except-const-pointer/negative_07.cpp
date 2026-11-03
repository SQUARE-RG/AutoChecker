struct Limits {
    int const maximum = 100; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
};

int main() {
    Limits limits;
    return limits.maximum;
}
