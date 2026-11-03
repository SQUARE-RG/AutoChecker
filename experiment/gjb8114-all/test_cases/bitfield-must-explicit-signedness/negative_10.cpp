struct {
    long int low : 4; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
} data;

int main() {
    data.low = 1;
    return 0;
}
