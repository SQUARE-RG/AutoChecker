int main() {
    int values[3] = {1, 2, 3}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-1]
    return values[0];
}
