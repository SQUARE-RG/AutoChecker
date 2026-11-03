constexpr bool high = true;
constexpr bool low = false;

static_assert(high && !low);

int main() {
    return 0;
}
