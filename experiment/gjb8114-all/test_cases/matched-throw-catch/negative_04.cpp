class A {};
class B {};

int main() {
    try {
        throw A(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
    } catch (const B&) {
    }
    return 0;
}
