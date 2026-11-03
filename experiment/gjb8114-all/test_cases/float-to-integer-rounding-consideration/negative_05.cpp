void consumeAsInt(int value) {
    (void)value;
}

int main() {
    double reading = 8.75;
    consumeAsInt(reading); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-10-1]
    return 0;
}
