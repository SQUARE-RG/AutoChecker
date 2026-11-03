struct Base {
    int base_value;
    Base() : base_value(1) {}
};
struct Derived : Base {
    int derived_value;
    Derived() : Base(), derived_value(2) {}
};
int main() {
    Derived object;
    try {
        throw object;
    }
    catch (Base base) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-1]
        return base.base_value;
    }
    catch (Derived derived) {
        return derived.derived_value;
    }
}
