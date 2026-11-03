int decide(bool flag) {
    int result = 0;
    switch (flag)
    {
        case true:
            result = 1;
            break;
        case false:
            result = 0;
            break;
        default:
            result = -1;
            break;
    }
    return result;
}

int main() {
    return decide(true);
}
