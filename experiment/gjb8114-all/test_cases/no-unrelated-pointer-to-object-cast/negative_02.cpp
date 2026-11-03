class Target {
public:
    Target() : value(0) {}
    int value;
};

int main() {
    double number = 3.14;
    Target* target = reinterpret_cast<Target*>(&number); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-1]
    (void)target;
    return 0;
}
