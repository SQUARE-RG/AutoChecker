namespace {
int unused_transformer(int value) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-3]
    return value * 2;
}
}

int main() {
    return 0;
}
