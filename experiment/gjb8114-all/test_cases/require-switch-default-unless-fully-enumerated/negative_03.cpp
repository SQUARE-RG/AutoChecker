enum class Color { Red, Green, Blue };

int classify(Color c) {
    int result = 0;
    switch (c) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-6]
    {
        case Color::Red:
            result = 1;
            break;
        case Color::Green:
            result = 2;
            break;
    }
    return result;
}

int main() {
    return classify(Color::Red);
}
