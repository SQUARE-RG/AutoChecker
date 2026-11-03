int drainConstant() {
    int attempts = 0;
    while (2) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-9-1]
        ++attempts;
        if (attempts >= 3) {
            break;
        }
    }
    return attempts;
}

int main() {
    return drainConstant();
}
