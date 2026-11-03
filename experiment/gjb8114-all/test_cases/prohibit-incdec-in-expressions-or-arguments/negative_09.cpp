int main() {
    int data[4] = {1, 2, 3, 4};
    int index = 0;
    data[index++] = 9; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    return data[0];
}
