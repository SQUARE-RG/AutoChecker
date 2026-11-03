namespace ex {
class Base {};
class Derived : public Base {};
}

void test() {
    try {
        throw ex::Derived();
    }
    catch (ex::Base& b) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
    }
    catch (ex::Derived& d) {
    }
}

int main() {
    test();
    return 0;
}
