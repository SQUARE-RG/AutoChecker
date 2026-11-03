// Lambda function with a small body, below the statement limit.
auto small_lambda = [](int x) {
    int y = x * 2;
    if (y < 0) {
        y = -y;
    }
    y += 1;
    return y;
};

int main() {
    return small_lambda(3);
}
