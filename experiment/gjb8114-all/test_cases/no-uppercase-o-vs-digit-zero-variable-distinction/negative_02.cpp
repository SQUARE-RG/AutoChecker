struct SpeedData {
    int speedO;
    int speed0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]
};

int main() {
    SpeedData data{1, 2};
    return data.speedO + data.speed0;
}
