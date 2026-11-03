int main() {
    int x = 3, y = 4, z = 5;
    while ((x > y) ^ (y < z)) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
        x = 10;
        break;
    }
    return 0;
}
