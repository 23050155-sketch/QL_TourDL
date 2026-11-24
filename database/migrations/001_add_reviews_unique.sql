
-- =====================================================
-- Project: HTTT16 - Quan Ly Tour Du Lich Noi Dia
-- Migration: 001_add_reviews_unique
-- Description: Moi khach hang chi danh gia mot lan
--              cho moi tour du lich
-- =====================================================

USE quan_ly_tour_du_lich;

ALTER TABLE reviews
ADD CONSTRAINT uq_reviews_user_tour
UNIQUE (user_id, tour_id);
