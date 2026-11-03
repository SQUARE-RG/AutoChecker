int connect(int timeout_ms = 3000) {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-1-6]
    return timeout_ms;
}

int main() {
    return connect();
}
