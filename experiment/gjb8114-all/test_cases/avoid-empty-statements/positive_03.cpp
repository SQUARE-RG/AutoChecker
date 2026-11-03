int labeled_nonempty(bool flag) {
    int result = 0;
    if (flag) {
        goto done;
    }
    result = 1;
done:
    result += 0;
    return result;
}
