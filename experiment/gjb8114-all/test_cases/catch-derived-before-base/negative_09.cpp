class Base {};
class Derived : public Base {};

void test() {
    try {
        throw Derived();
    }
    catch (Base&) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
    }
    catch (Derived&) {
    }
}

int main() {
    test();
    return 0;
}
