int switch_nonempty(int value) {
    int result = 0;
    switch (value) {
    case 0:
        result += 0;
        break;
    default:
        result = 1;
        break;
    }
    return result;
}
