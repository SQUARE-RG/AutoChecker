namespace ex {
class Base {};
class Derived : public Base {};
}

void test() {
    try {
        throw ex::Derived();
    }
    catch (ex::Derived& d) {
    }
    catch (ex::Base& b) {
    }
}

int main() {
    test();
    return 0;
}
