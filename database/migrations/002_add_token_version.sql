
-- =====================================================
-- Project: HTTT16 - Quan Ly Tour Du Lich Noi Dia
-- Migration: 002_add_token_version
-- Description: Bo sung phien ban JWT cho tai khoan
-- =====================================================

USE quan_ly_tour_du_lich;

ALTER TABLE users
ADD COLUMN token_version INT UNSIGNED
NOT NULL DEFAULT 1
AFTER status;
