void Process(short value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-1]
    (void)value;
}

int main() {
    Process(7);
    return 0;
}
