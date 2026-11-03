// negative_09.cpp
int main() {
    auto compute = [](int fSpeedO, int fSpeed0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-10]
        return fSpeedO + fSpeed0;
    };
    return compute(1, 2);
}
