int main() {
    double value = 3.14;
    int truncated = (int)value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
    return truncated;
}
