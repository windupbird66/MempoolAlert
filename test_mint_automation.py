import logging

if current_height is not None:
    next_block = current_height + 1
    distance = TARGET_BLOCK_HEIGHT - next_block  # 使用等待过块的区块来计算距离
    logging.info(f"当前区块高度: {current_height} | 等待过块区块: {next_block} | 距离目标区块: {distance}")
    
    if current_height >= TARGET_BLOCK_HEIGHT:
        if str(TARGET_BLOCK_HEIGHT) not in minted_blocks:
            logging.warning(f"当前区块 {current_height} 已经达到或超过目标区块 {TARGET_BLOCK_HEIGHT}，无法提交交易，跳过mint操作")
        else:
            logging.info(f"已在目标区块 {TARGET_BLOCK_HEIGHT} 执行过mint操作")
        break
    elif current_height == TARGET_BLOCK_HEIGHT - 1:
        # 当前区块是目标区块减1，说明下一个区块就是目标区块，现在应该执行mint
        if str(TARGET_BLOCK_HEIGHT) not in minted_blocks:
            logging.info(f"当前区块 {current_height}，下一个区块 {TARGET_BLOCK_HEIGHT} 将是目标区块，开始执行自动化铸造步骤...")
            automate_minting_steps(YOUR_PRIVATE_KEY, RECEIVE_ADDRESS, str(GAS_FEE_RATE))
            logging.info("自动化铸造步骤执行完毕。")
            minted_blocks[str(TARGET_BLOCK_HEIGHT)] = True
            save_mint_status(minted_blocks)
            break  # mint完成后退出
        else:
            logging.info(f"已在目标区块 {TARGET_BLOCK_HEIGHT} 执行过mint操作，跳过")
            break
    else:
        logging.info(f"继续监控中...") 