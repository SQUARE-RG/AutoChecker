class Base {};
class Derived : public Base {};

void test() {
    try {
        throw Derived();
    }
    catch (Derived&) {
    }
    catch (Base&) {
    }
}

int main() {
    test();
    return 0;
}
