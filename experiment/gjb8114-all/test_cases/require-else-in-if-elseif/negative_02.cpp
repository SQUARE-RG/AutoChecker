int classify(int value) {
    int result = 0;
    if (value == 1) result = 10; else if (value == 2) result = 20; else if (value == 3) result = 30; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-1]
    return result;
}

int main() {
    return classify(0);
}
