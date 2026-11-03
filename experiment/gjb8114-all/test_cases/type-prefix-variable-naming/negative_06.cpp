// negative_06.cpp
// Intent: lambda parameter with explicit int type is missing the i type prefix.
int main() {
    return [](int value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-1]
        return value + 1;
    }(1);
}
