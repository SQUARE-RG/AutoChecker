using Func = void (*)(int);

int main() {
    auto lambda = [](int) {};
    Func f = (Func)lambda; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-5-1]
    f(42);
    return 0;
}
