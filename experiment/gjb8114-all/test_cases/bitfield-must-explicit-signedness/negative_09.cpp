struct Data {
    short int value : 3; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-11]
};

int main() {
    Data data{};
    data.value = 1;
    return 0;
}
