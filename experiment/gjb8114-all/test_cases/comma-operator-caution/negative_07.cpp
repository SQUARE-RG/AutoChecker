int main() {
    int step = 0;
    int total = 0;
    while ((step = step + 1, step <= 3)) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
        total += step;
    }
    return total;
}
