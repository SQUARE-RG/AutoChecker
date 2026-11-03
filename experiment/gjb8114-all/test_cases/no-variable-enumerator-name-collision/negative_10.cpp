enum Color { red, green, blue };

int main() {
    auto value = [red = 0]() { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
        return red;
    };
    return value();
}
