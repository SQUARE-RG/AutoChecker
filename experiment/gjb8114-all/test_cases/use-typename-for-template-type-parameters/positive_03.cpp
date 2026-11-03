template <typename T>
using identity_t = T;

int main() {
    identity_t<int> value = 42;
    return value;
}
