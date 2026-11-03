int read(int const value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]
    return value;
}

int main() {
    return read(42);
}
